def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def cell_ok(x, y):
        return (x, y) not in obstacles

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or not cell_ok(nx, ny):
            continue

        if resources:
            # nearest resource; tie-break by keeping distance from opponent
            md = 10**9
            for rx, ry in resources:
                d = man(nx, ny, rx, ry)
                if d < md:
                    md = d
            od = man(nx, ny, ox, oy)
            # maximize: prefer smaller md (encode as negative), prefer larger od
            key = (-md, od, dx, dy)
        else:
            # no resources: maximize distance from opponent
            od = man(nx, ny, ox, oy)
            key = (od, -(abs(nx - (w - 1) // 2) + abs(ny - (h - 1) // 2)), dx, dy)

        if best is None or key > best[0]:
            best = (key, [dx, dy])

    if best is None:
        return [0, 0]
    return best[1]