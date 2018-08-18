"""Classes"""


class A:

    @classmethod
    def foo(cls, name):
        print(f"A: {name}")


class B(A):

    @classmethod
    def foo(cls, name):
        super().foo(name)
        print(f"B: {name}")


x = B()

x.foo("bar")

print("Done")
