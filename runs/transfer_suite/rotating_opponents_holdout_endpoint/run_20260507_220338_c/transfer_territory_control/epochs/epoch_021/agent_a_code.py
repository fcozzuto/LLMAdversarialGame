def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = (observation.get("opponent_position") or (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    my = set((int(x), int(y)) for x, y in observation.get("self_territory") or [])
    opp = set((int(x), int(y)) for x, y in observation.get("opponent_territory") or [])
    un = set((int(x), int(y)) for x, y in observation.get("unclaimed_cells") or [])
    obstacles = set((int(x), int(y)) for x, y in observation.get("obstacles") or [])

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    if (sx, sy) in obstacles:
        obstacles.discard((sx, sy))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dcur = abs(sx - ox) + abs(sy - oy)

    bestv = -10**18
    best = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        dist = abs(nx - ox) + abs(ny - oy)
        is_un = (nx, ny) in un
        is_my = (nx, ny) in my
        is_opp = (nx, ny) in opp

        v = 0
        v += 6.0 if is_un else 0.0
        v += 2.0 if is_my else 0.0
        v += 3.5 if is_opp else 0.0

        v += 1.25 * dist
        if dcur <= 3:
            v += 1.5 * (dist - dcur)  # back away when close

        if is_opp and dist <= dcur:
            v -= 5.0  # avoid getting swept back unless we move away

        if dx == 0 and dy == 0:
            v -= 0.2  # small bias to move

        if v > bestv:
            bestv = v
            best = (dx, dy)
    return [int(best[0]), int(best[1])]