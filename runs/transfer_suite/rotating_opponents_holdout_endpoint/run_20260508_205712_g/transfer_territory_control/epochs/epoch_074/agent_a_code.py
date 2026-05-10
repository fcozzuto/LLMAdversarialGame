def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    unclaimed = []
    for p in (observation.get("unclaimed_cells") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                unclaimed.append((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                resources.append((x, y))

    # Opponent and self territories (for flip tendency)
    oppT = set()
    for p in (observation.get("opponent_territory") or []):
        if p and len(p) >= 2:
            oppT.add((int(p[0]), int(p[1])))
    selfT = set()
    for p in (observation.get("self_territory") or []):
        if p and len(p) >= 2:
            selfT.add((int(p[0]), int(p[1])))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    inb = lambda x, y: 0 <= x < w and 0 <= y < h

    center = (w // 2, h // 2)
    # Target selection
    if unclaimed:
        tx, ty = min(unclaimed, key=lambda t: (abs(t[0] - sx) + abs(t[1] - sy), t[0], t[1]))
    elif resources:
        tx, ty = min(resources, key=lambda t: (abs(t[0] - sx) + abs(t[1] - sy), t[0], t[1]))
    else:
        tx, ty = center

    # Score candidate moves
    best = None
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        man_to_target = abs(nx - tx) + abs(ny - ty)
        man_to_opp = abs(nx - ox) + abs(ny - oy)

        # Reward immediate claim opportunities / penalize stepping into opponent territory (flip enabled)
        reward = 0
        if (nx, ny) in unclaimed:
            reward += 80
        if (nx, ny) in resources:
            reward += 25
        if (nx, ny) in oppT:
            # flipping is good; scale by whether it likely expands control (closer to target & away from opp)
            reward += 55 - (man_to_opp // 2)
        if (nx, ny) in selfT:
            reward -= 5  # prefer expansion

        # Main objective: reduce distance to target while not walking straight into opponent pressure
        score = reward - (man_to_target * 3) + (man_to_opp * 1)

        # Deterministic tie-break
        move = (dx, dy)
        if best_score is None or score > best_score or (score == best_score and move < best):
            best_score = score
            best = move

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]