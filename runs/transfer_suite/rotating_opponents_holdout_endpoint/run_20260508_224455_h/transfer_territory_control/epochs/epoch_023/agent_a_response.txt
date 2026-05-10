def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8)) or 8
    h = int(observation.get("grid_height", 8)) or 8

    obstacles = set(map(tuple, observation.get("obstacles", []) or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", []) or []))
    self_terr = set(map(tuple, observation.get("self_territory", []) or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory", []) or []))

    dirs = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1), (0, 0)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def md(a, b, c, d): return abs(a - c) + abs(b - d)

    # Limit target set for speed/determinism
    un_list = list(unclaimed)
    un_list.sort(key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), p[0], p[1]))
    un_list = un_list[:12] if un_list else []

    # Find current "frontier" proxy: closest unclaimed to us
    if un_list:
        nearest_un_to_us = min(un_list, key=lambda p: md(sx, sy, p[0], p[1]))
        ux, uy = nearest_un_to_us
    else:
        ux, uy = ox, oy

    best = [0, 0]
    best_sc = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if (nx, ny) == (ox, oy):
            continue

        sc = 0
        if (nx, ny) in unclaimed:
            sc += 1300
        elif (nx, ny) in opp_terr:
            sc += 650
        elif (nx, ny) in self_terr:
            sc += 250
        else:
            sc += 40

        # Prefer progressing toward nearby unclaimed
        sc += 18 * (md(sx, sy, ux, uy) - md(nx, ny, ux, uy))

        # Also consider local nearest-unclaimed improvement
        if un_list:
            cur_near = min(un_list, key=lambda p: md(sx, sy, p[0], p[1]))
            cand_near = min(un_list, key=lambda p: md(nx, ny, p[0], p[1]))
            sc += 10 * (md(sx, sy, cur_near[0], cur_near[1]) - md(nx, ny, cand_near[0], cand_near[1]))

        # Reduce risk from opponent proximity; allow capture only if it improves progress
        sc -= 6 * md(nx, ny, ox, oy)

        if dx == 0 and dy == 0:
            sc -= 30

        if sc > best_sc or (sc == best_sc and (dx, dy) < (best[0], best[1])):
            best_sc = sc
            best = [dx, dy]

    return [int(best[0]), int(best[1])]