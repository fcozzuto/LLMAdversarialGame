def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocks = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocks.add((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    opp_terr = [(int(x), int(y)) for (x, y) in (observation.get("opponent_territory") or []) if isinstance(x, (int, float)) and isinstance(y, (int, float))]
    unclaimed = [(int(x), int(y)) for (x, y) in (observation.get("unclaimed_cells") or []) if isinstance(x, (int, float)) and isinstance(y, (int, float))]

    opp_set = set(opp_terr)
    un_set = set(unclaimed)
    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocks

    if not opp_terr and not unclaimed:
        return [0, 0]

    best_move = [0, 0]
    best_score = -10**18

    # Prefer stepping into opponent territory (flipping), otherwise approach nearest opponent territory.
    # If no opponent territory visible, sweep toward unclaimed, especially edges.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        score = 0

        if (nx, ny) in opp_set:
            score += 5000  # direct flip
        else:
            if opp_terr:
                md = 10**9
                for tx, ty in opp_terr:
                    d = abs(nx - tx) + abs(ny - ty)
                    if d < md:
                        md = d
                score += -120 * md  # closer to opponent territory is better

        # If we're not flipping, try to get to the frontier: cells adjacent to opponent territory.
        if opp_terr and (nx, ny) not in opp_set:
            adj = 0
            for tx, ty in opp_terr:
                if abs(nx - tx) <= 1 and abs(ny - ty) <= 1 and (nx, ny) != (tx, ty):
                    adj += 1
            score += 25 * adj

        # Unclaimed pressure: prefer edges to counter sweeper path.
        if unclaimed and (nx, ny) not in opp_set:
            if (nx, ny) in un_set:
                score += 800
            else:
                edge_bonus = (1 if (nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1) else 0)
                if edge_bonus:
                    score += 40
                # small attraction toward nearest unclaimed
                md2 = 10**9
                for ux, uy in unclaimed:
                    d = abs(nx - ux) + abs(ny - uy)
                    if d < md2:
                        md2 = d
                score += -10 * md2

        # Keep moving generally toward opponent position to maintain initiative.
        score += -2 * (abs(nx - ox) + abs(ny - oy))
        score += -1 * (dx == 0 and dy == 0)

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move