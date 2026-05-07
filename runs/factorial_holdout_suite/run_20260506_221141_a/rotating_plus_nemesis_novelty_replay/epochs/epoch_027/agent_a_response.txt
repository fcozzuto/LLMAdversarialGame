def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < gw and 0 <= py < gh:
                obstacles.add((px, py))

    resources = []
    for r in (observation.get("resources") or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < gw and 0 <= ry < gh and (rx, ry) not in obstacles:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # New policy vs previous: prioritize maximizing (opponent lead - self lead) and, failing that,
    # maximize separation while moving toward the best resource.
    best = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        lead = od - sd  # positive => we arrive earlier
        # Make exact arrival ties slightly prefer closer-to-opponent avoidance
        val = lead * 2 - sd
        if best is None or val > best[0] or (val == best[0] and (sd < best[1])):
            best = (val, sd, od, rx, ry, lead)

    _, _, _, tx, ty, lead = best

    # Candidate moves: choose move that best progresses to target; if can't secure first, bias away from opponent.
    want_away = lead < 1
    best_move = [0, 0]
    best_score = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if (nx, ny) in obstacles or not (0 <= nx < gw and 0 <= ny < gh):
                continue
            ds = man(nx, ny, tx, ty)
            do = man(nx, ny, ox, oy)
            # Higher score is better
            score = -ds * 3
            if want_away:
                score += do * 1  # separation
            else:
                score += (do - man(sx, sy, ox, oy)) * 0  # no-op, keep deterministic
            # Small tie-break: prefer staying still less if it doesn't hurt
            score += (-(abs(dx) + abs(dy)) * 0.01)
            if best_score is None or score > best_score:
                best_score = score
                best_move = [dx, dy]

    return best_move