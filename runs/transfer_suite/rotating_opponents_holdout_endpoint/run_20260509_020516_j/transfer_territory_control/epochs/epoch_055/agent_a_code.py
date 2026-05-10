def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(v):
        s = set()
        for p in v or []:
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < W and 0 <= y < H:
                    s.add((x, y))
        return s

    obstacles = to_set(observation.get("obstacles"))
    myT = to_set(observation.get("self_territory"))
    oppT = to_set(observation.get("opponent_territory"))
    unC = to_set(observation.get("unclaimed_cells"))
    res = to_set(observation.get("resources"))

    def inb(x, y): return 0 <= x < W and 0 <= y < H
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    def dist(a, b, c, d): return abs(a - c) + abs(b - d)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    dirs = [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]
    my_near_opp = 0
    if myT:
        for x, y in myT:
            for dx, dy in dirs:
                if (x+dx, y+dy) in oppT:
                    my_near_opp = 1
                    break
            if my_near_opp: break

    targets = res or unC
    best = [0, 0]
    bestv = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        v = 0
        if (nx, ny) in res: v += 2000
        if (nx, ny) in unC: v += 1400
        if (nx, ny) in oppT: v += 900

        d_opp_now = dist(nx, ny, ox, oy)
        d_opp_cur = dist(sx, sy, ox, oy)
        if d_opp_now < d_opp_cur:
            v -= 55
        else:
            v += 10

        if myT:
            near_my = 0
            for tx, ty in dirs:
                if (nx+tx, ny+ty) in myT:
                    near_my = 1
                    break
            v += 18 * near_my

        if oppT:
            near_opp = 0
            for tx, ty in dirs:
                if (nx+tx, ny+ty) in oppT:
                    near_opp = 1
                    break
            v -= 70 * near_opp if my_near_opp else 30 * near_opp

        if targets:
            if targets is res:
                tset = res
            else:
                tset = unC
            md = 10**9
            for tx, ty in tset:
                d = dist(nx, ny, tx, ty)
                if d < md: md = d
            v += (1200 - 150 * md) if tset else 0

        if v > bestv or (v == bestv and (dx, dy) == (0, 0) and best != [0, 0]):
            bestv = v
            best = [dx, dy]

    return best