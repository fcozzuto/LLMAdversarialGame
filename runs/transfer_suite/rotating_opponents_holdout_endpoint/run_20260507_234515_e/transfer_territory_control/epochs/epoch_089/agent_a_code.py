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

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        score = 0
        if (nx, ny) in oppT:
            score += 100
        elif (nx, ny) in selfT:
            score += 15
        if (nx, ny) in unclaimed:
            score += 60
        md = abs(nx - ox) + abs(ny - oy)
        score += -md
        if best is None or score > best_score:
            best_score = score
            best = [dx, dy]
    return best if best is not None else [0, 0]