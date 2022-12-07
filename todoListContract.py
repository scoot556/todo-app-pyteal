from pyteal import *

def approval_program():
    handle_creation = Seq([
        App.globalPut(Bytes("Total_Complete"), Int(0)),
        Return(Int(1))
    ])

    handle_optin = Return(Int(1))
    handle_closeout = Return(Int(0))
    handle_updateapp = Return(Int(0))
    handle_deleteapp = Return(Int(0))
    scratchCount = ScratchVar(TealType.uint64)
    localCount = ScratchVar(TealType.uint64)
    localTodo = ScratchVar(TealType.bytes)



    add_local_todo = Seq([
        localTodo.store(App.localGet(Txn.sender(), Bytes("Todo"))),
        App.localPut(Txn.sender(), Txn.application_args[1], Txn.application_args[2]),
        Return(Int(1))
    ])

    complete_local_todo = Seq([
        localTodo.store(App.localGet(Txn.sender(), Bytes("Todo"))),
        scratchCount.store(App.globalGet(Bytes("Total_Complete"))),
        localCount.store(App.localGet(Txn.sender(), Bytes("Count"))),
        App.localPut(Txn.sender(), Bytes("Count"), localCount.load() + Int(1)),
        App.globalPut(Bytes("Total_Complete"), scratchCount.load() + Int(1)),
        App.localDel(Txn.sender(), Txn.application_args[1]),
        Return(Int(1))
    ])

    handle_noop = Seq(
        Assert(Global.group_size() == Int(1)),
        Cond(
            [Txn.application_args[0] == Bytes("Add_Local_Todo"), add_local_todo],
            [Txn.application_args[0] == Bytes("Complete_Local_Todo"), complete_local_todo]
        )
    )

    program = Cond(
        [Txn.application_id() == Int(0), handle_creation],
        [Txn.on_completion() == OnComplete.OptIn, handle_optin],
        [Txn.on_completion() == OnComplete.CloseOut, handle_closeout],
        [Txn.on_completion() == OnComplete.UpdateApplication, handle_updateapp],
        [Txn.on_completion() == OnComplete.DeleteApplication, handle_deleteapp],
        [Txn.on_completion() == OnComplete.NoOp, handle_noop]
    )

    return compileTeal(program, Mode.Application, version=5)

def clear_state_program():
    program = Return(Int(1))
    return compileTeal(program, Mode.Application, version=5)

appFile = open('approval.teal', 'w')
appFile.write(approval_program())
appFile.close()

appFile = open('clear.teal', 'w')
appFile.write(clear_state_program())
appFile.close()
