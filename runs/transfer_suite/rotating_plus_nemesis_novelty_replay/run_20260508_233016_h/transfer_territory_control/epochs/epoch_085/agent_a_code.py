def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    unclaimed = observation.get("unclaimed_cells") or []
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if (0 <= nx < w and 0 <= ny < h) and (nx, ny) in obstacles:
            # still allow but will be scored low; engine will keep in place if invalid
            pass

    best_target = None
    if unclaimed:
        # pick a frontier cell: prefer near us and near opponent, but avoid our own territory
        scored = []
        for c in unclaimed:
            x, y = c
            if (x, y) in selfT:
                continue
            # If opponent already controls it, prefer attacking there
            attack_bonus = 12 if (x, y) in oppT else 0
            center_bias = (abs(x - (w - 1) / 2) + abs(y - (h - 1) / 2)) * 0.1
            score = (man(x, y, sx, sy) * 2.2) + man(x, y, ox, oy) + center_bias - attack_bonus
            scored.append((score, x, y))
        scored.sort()
        if scored:
            best_target = (scored[0][1], scored[0][2])
    if best_target is None:
        # fall back to moving toward nearest opponent frontier: nearest unclaimed adjacent to opponent territory
        if oppT and unclaimed:
            opp_front = set()
            for (x, y) in oppT:
                for dx, dy in candidates:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h:
                        if (nx, ny) not in selfT and (nx, ny) not in oppT:
                            opp_front.add((nx, ny))
            candidates_un = [c for c in unclaimed if tuple(c) in opp_front]
            if candidates_un:
                best_target = min(candidates_un, key=lambda c: man(c[0], c[1], sx, sy))
        if best_target is None:
            best_target = (w // 2, h // 2)

    tx, ty = best_target
    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        dist_now = man(sx, sy, tx, ty)
        dist_next = man(nx, ny, tx, ty)
        progress = dist_now - dist_next

        cell_bonus = 0
        if (nx, ny) in oppT:
            cell_bonus += 30  # stepping into enemy territory to flip
        if (nx, ny) in selfT:
            cell_bonus -= 2   # prefer expansion over already-owned
        if (nx, ny) not in selfT and (nx, ny) not in oppT:
            cell_bonus += 6   # unclaimed/neutral generally good

        # slight bias to keep away from opponent when not targeting them
        safety = -0.08 * man(nx, ny, ox, oy)

        # discourage standing still unless no progress options
        stay_pen = -0.5 if (dx == 0 and dy == 0) else 0

        score = progress * 5 + cell_bonus + safety + stay_pen
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move