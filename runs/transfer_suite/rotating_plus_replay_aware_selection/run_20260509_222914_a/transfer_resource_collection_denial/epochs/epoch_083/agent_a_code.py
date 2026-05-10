def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    if w <= 0 or h <= 0:
        return [0, 0]

    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obs.add((ax, ay))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obs:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    # Prefer moves that secure resources earlier than opponent; break ties by "safe" lines.
    best_score = None
    best_delta = [0, 0]

    occupied_adj = set(obs)
    for ax, ay in obs:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            nx, ny = ax + dx, ay + dy
            if 0 <= nx < w and 0 <= ny < h:
                occupied_adj.add((nx, ny))

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue

        # Main objective: win resources by distance advantage.
        score = 0
        for rx, ry in resources:
            d_me = md(nx, ny, rx, ry)
            d_op = md(ox, oy, rx, ry)
            # If we can reach no later than opponent, prioritize strongly.
            adv = d_op - d_me
            if adv > 0:
                score += 50 + 5 * adv
            elif adv == 0:
                score += 18
            else:
                score += -3 * (-adv)
            # Small incentive to be closer, even if not beating opponent now.
            score += -0.2 * d_me

        # Deterministic small "steering" to avoid getting stuck in a row-sweep:
        # Prefer keeping movement aligned with x-direction toward opponent side.
        dirx = 1 if ox > sx else (-1 if ox < sx else 0)
        steer = 0
        if dirx != 0:
            steer = dx * dirx * 2
        score += steer

        # Safety: avoid moving adjacent to obstacles if alternatives exist.
        if (nx, ny) in occupied_adj:
            score -= 4

        # Capture immediate resource: strongest tie-break.
        if (nx, ny) in resources:
            score += 200

        if best_score is None or score > best_score:
            best_score = score
            best_delta = [dx, dy]

    return [int(best_delta[0]), int(best_delta[1])]