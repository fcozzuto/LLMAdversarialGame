def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    resources = observation.get("resources") or []
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    if not resources:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            d = abs(nx - cx) + abs(ny - cy)
            if best is None or d < best[0]:
                best = (d, dx, dy)
        return [best[1], best[2]]

    # Tighten urgency when few resources remain
    rem = observation.get("remaining_resource_count")
    urgency = 1.0 if rem is None else (1.0 + (12 - max(0, rem)) / 10.0)

    best_val = None
    best_move = (0, 0)
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy

        # Score by best resource "opportunity" from this move
        val = -10**18
        for rx, ry in resources:
            myd = abs(nx - rx) + abs(ny - ry)
            oppd = abs(ox - rx) + abs(oy - ry)
            if myd == 0:
                v = 10**6  # immediate pickup
            else:
                lead = (oppd - myd)  # positive means we are closer
                # Prefer taking leads; also prefer denying nearby resources even if behind a bit
                v = (lead * 120.0 * urgency) - (myd * 8.0) + (oppd * 1.5)
                # If both can reach soon, prioritize the one we can beat
                if myd <= 2 and oppd <= 2:
                    v += lead * 60.0

            # Slightly bias toward reducing overall distance to resources (deterministic tie-breaker)
            v -= (abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0)) * 0.5
            if v > val:
                val = v

        # Deterministic tie-break: lexicographic order on (dx, dy) after val
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]