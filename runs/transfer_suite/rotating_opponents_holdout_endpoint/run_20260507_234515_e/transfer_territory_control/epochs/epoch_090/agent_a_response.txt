def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        try:
            obstacles.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    selfT = set(tuple(map(int, c)) for c in (observation.get("self_territory") or []))
    oppT = set(tuple(map(int, c)) for c in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(map(int, c)) for c in (observation.get("unclaimed_cells") or []))

    cx, cy = w // 2, h // 2
    un_list = list(unclaimed)
    if un_list:
        # Prefer unclaimed near center, but also slightly prefer those closer to us than opponent.
        un_list.sort(key=lambda t: (abs(t[0] - cx) + abs(t[1] - cy),
                                     (abs(t[0] - sx) + abs(t[1] - sy)) - (abs(t[0] - ox) + abs(t[1] - oy)),
                                     t[0], t[1]))
        target = un_list[0]
    else:
        target = (cx, cy)

    dirs = [(-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)]

    best = [0, 0]
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        score = 0
        if (nx, ny) in oppT:
            score += 200  # likely flip on entry
        elif (nx, ny) in selfT:
            score += 10
        if (nx, ny) in unclaimed:
            score += 120

        # Head to target; also keep pressure on opponent by reducing their distance.
        score += - (abs(nx - target[0]) + abs(ny - target[1])) * 3
        score += - (abs(nx - ox) + abs(ny - oy)) * 0.5

        # Slightly avoid stepping into opponent-owned cells unless it flips.
        if (nx, ny) in oppT:
            score += 5

        # Deterministic tie-break: prefer lower dx, then lower dy, then staying centered.
        if score > best_score or (score == best_score and (dx, dy, abs(nx - cx) + abs(ny - cy)) < (best[0], best[1], abs(best[0]) + abs(best[1]))):
            best_score = score
            best = [dx, dy]

    return [int(best[0]), int(best[1])]