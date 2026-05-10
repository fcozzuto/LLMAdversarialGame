def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    un_list = list(unclaimed)
    has_un = len(un_list) > 0
    best = (0, 0)
    best_score = -10**18

    for ddx, ddy in dirs:
        nx, ny = sx + ddx, sy + ddy
        if not ok(nx, ny):
            continue
        nxt = (nx, ny)
        score = 0

        if nxt in opp_t:
            score += 800
        elif nxt in unclaimed:
            score += 60
        elif nxt in self_t:
            score += 8
        else:
            score += 2

        score += 3 if nxt == (sx, sy) else 0

        d_opp = man((nx, ny), (ox, oy))
        score += (40 - d_opp) * 0.5

        if has_un:
            d_un = 10**9
            for ux, uy in un_list:
                d = abs(ux - nx) + abs(uy - ny)
                if d < d_un:
                    d_un = d
                    if d_un == 0:
                        break
            score += (20 - d_un) * 2.0
        else:
            score += (30 - d_opp) * 2.0

        if score > best_score:
            best_score = score
            best = (ddx, ddy)

    return [int(best[0]), int(best[1])]