def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    unclaimed = set()
    for p in observation.get("unclaimed_cells", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unclaimed.add((x, y))

    self_terr = set()
    for p in observation.get("self_territory", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                self_terr.add((x, y))

    opp_terr = set()
    for p in observation.get("opponent_territory", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                opp_terr.add((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_score = -10**18

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    adj8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        dist_opp = abs(nx - ox) + abs(ny - oy)
        dist_opp_score = dist_opp * 1.5  # keep away from opponent to avoid easy counter-expansion

        bonus_unclaimed = 0
        if (nx, ny) in unclaimed:
            bonus_unclaimed = 18

        # prefer frontier expansion: stay/expand near our territory cluster
        frontier = 0
        if not self_terr:
            frontier = 0
        else:
            for ax, ay in adj8:
                px, py = nx + ax, ny + ay
                if (px, py) in self_terr:
                    frontier = 6
                    break

        # entering opponent territory can flip; do it only if it also increases distance from opponent
        enter_opp = 0
        if (nx, ny) in opp_terr:
            enter_opp = -10  # default: avoid
            if dist_opp >= 3:
                enter_opp = 6  # sometimes it's worth contesting far while capturing adjacent unclaimed

        # slight tie-break toward center to avoid getting stuck on edges
        center_x, center_y = (w - 1) / 2.0, (h - 1) / 2.0
        center_score = -0.2 * (abs(nx - center_x) + abs(ny - center_y))

        score = dist_opp_score + bonus_unclaimed + frontier + enter_opp + center_score

        # deterministic tie-break
        if score > best_score or (score == best_score and (dx, dy) < tuple(best_move)):
            best_score = score
            best_move = [dx, dy]

    return best_move