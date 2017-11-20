import cadquery


def intersect(wp1, wp2, combine=True, clean=True):
    """
    Return geometric intersection between 2 cadquery.Workplane instances by
    exploiting.
    A n B = (A u B) - ((A - B) u (B - A))
    """
    solidRef = wp1.findSolid(searchStack=True, searchParents=True)

    if solidRef is None:
        raise ValueError("Cannot find solid to intersect with")
    solidToIntersect = None

    if isinstance(wp2, cadquery.CQ):
        solidToIntersect = wp2.val()
    elif isinstance(wp2, cadquery.Solid):
        solidToIntersect = wp2
    else:
        raise ValueError("Cannot intersect type '{}'".format(type(wp2)))

    newS = solidRef.intersect(solidToIntersect)

    if clean:
        newS = newS.clean()

    if combine:
        solidRef.wrapped = newS.wrapped

    return wp1.newObject([newS])

    #cp = lambda wp: wp.translate((0, 0, 0))
    #neg1 = cp(wp1).cut(wp2)
    #neg2 = cp(wp2).cut(wp1)
    #neg = neg1.union(neg2)
    #return cp(wp1).union(wp2).cut(neg)


def copy(wp):
    return wp.translate((0, 0, 0))
