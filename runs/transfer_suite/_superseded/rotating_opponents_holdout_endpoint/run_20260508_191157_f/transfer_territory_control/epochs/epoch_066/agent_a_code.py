def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    own = set(tuple(t) for t in (observation.get("self_territory") or []))
    opp = set(tuple(t) for t in (observation.get("opponent_territory") or []))

    targets = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                targets.append((x, y))
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2 and len(targets) < 30:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                targets.append((x, y))

    def best_dir(tgt_list):
        best = None
        best_score = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                continue
            if tgt_list:
                d = 10**9
                for tx, ty in tgt_list:
                    dd = abs(nx - tx) + abs(ny - ty)
                    if dd < d:
                        d = dd
                # Prefer getting closer to targets; penalize moving into opponent territory
                score = d + (0 if (nx, ny) in own else 1) + (0 if (nx, ny) not in opp else -2)
            else:
                # No targets: advance toward opponent
                score = abs(nx - ox) + abs(ny - oy)
            if best_score is None or score < best_score:
                best_score = score
                best = (dx, dy)
        return best

    move = best_dir(targets if targets else None)
    if move is None:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [int(dx), int(dy)]
        return [0, 0]
    return [int(move[0]), int(move[1])]