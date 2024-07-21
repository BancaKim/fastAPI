import asyncio 

# async def : 비동기 함수를 정의하는 키워드. 호ㄹ 시 즉시 Future 객체 반환 
# Future 객체란? 
# 비동기 연산의 아직 완료되지 않은 결과를 나타냄
# 연산의 상태를 추적하고 완료 시 결과에 접근
# 성공, 실패 여부와 관계없이 최종 결과나 예외를 포함
# 연산 완료 후 실행될 콜백을 설정하는데 사용
# await : 비동기 함수 내에서 사용되며, 특정 비동기 연산이 완료될 때까지 함수의 실행을 일시적으로 중지하고 해당 연산의 완료를 기다림
#         비동기 연산이 완료될 때까지 현재 코루틴의 실행을 일시 정지. await 뒤에는 awaitable 객체가 위치해야 하며, 이는 일반적으로 asnyc def로 정의된 비동기 함수의 호출

async def func1():
    print("func1: Start")
    await asyncio.sleep(2) # 비동기로 2초간 대기
    print("func1: End")

async def func2():
    print("func2: Start")
    await asyncio.sleep(1) #비동기로 1초간 대기
    print("func2: End")

async def main():
    await asyncio.gather(func1(),func2()) #func1과 func2를 동시에 실행

    #이벤트 루프 : 프로그램의 진입점에서 실행 asyncio.run(main())과 같이 사용하여 주어진 코루틴을 실행하고 완료될 때까지의 이벤트 루프를 유지
    #asyncio.gather(*tasks)를 사용하여 여러 코루틴을 동시에 실행 가능. 이 함수는 모든 코루틴이 완료될 때 까지 기다린 후, 각 코루틴의 결과를 포함하는 리스트 반환
if __name__ == "__main__":
    asyncio.run(main())