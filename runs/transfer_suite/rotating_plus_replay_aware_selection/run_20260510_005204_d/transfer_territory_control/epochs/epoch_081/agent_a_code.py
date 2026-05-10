def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []) if p and len(p) >= 2)
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2)
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2)

    dirs8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def manh(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = (float("-inf"), 0, 0)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                nx, ny = sx, sy
                dx, dy = 0, 0

            if (nx, ny) in opp_terr:
                base = 60
            elif (nx, ny) in unclaimed:
                base = 40
            elif (nx, ny) in self_terr:
                base = 10
            else:
                base = 0

            adj_u = 0
            adj_o = 0
            for ddx, ddy in dirs8:
                tx, ty = nx + ddx, ny + ddy
                if 0 <= tx < w and 0 <= ty < h:
                    if (tx, ty) in unclaimed:
                        adj_u += 1
                    if (tx, ty) in opp_terr:
                        adj_o += 1

            d_opp = manh(nx, ny, ox, oy)
            value = base + adj_u * 3 - adj_o * 4 - d_opp * 0.05

            if value > best[0] or (value == best[0] and (dx, dy) < (best[1], best[2])):
                best = (value, dx, dy)

    return [int(best[1]), int(best[2])]