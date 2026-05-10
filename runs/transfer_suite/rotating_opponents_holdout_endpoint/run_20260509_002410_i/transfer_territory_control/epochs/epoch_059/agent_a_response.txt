def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    px, py = observation.get("opponent_position", (0, 0))
    sx, sy, px, py = int(sx), int(sy), int(px), int(py)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obs

    unclaimed = [(int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []) if inb(int(x), int(y)) and (int(x), int(y)) not in obs]
    opp_terr = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []) if inb(int(x), int(y)))
    my_terr = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []) if inb(int(x), int(y)))

    if not unclaimed and not opp_terr:
        return [0, 0]

    # Prefer contest squares near opponent territory (for counterclaims), but not already blocked by obstacles.
    adj_opp = set()
    for ox, oy in opp_terr:
        for dx, dy in dirs:
            nx, ny = ox + dx, oy + dy
            if valid(nx, ny) and (nx, ny) not in opp_terr:
                adj_opp.add((nx, ny))
    candidates = []
    if adj_opp:
        for c in unclaimed:
            if c in adj_opp:
                candidates.append(c)
    if not candidates:
        candidates = unclaimed[:] if unclaimed else list(opp_terr)

    # Also bias away from being too close to opponent position if already leading (territory control stability).
    sc = observation.get("scores") or {}
    my_score = float(sc.get(observation.get("self_name", "agent_a"), sc.get("agent_a", 0.0)))
    opp_score = float(sc.get(observation.get("opponent_name", "agent_b"), sc.get("agent_b", 0.0)))
    leading = my_score > opp_score

    # Deterministic: evaluate each possible move with a small heuristic.
    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Prefer cells closer to candidate contest points.
        if candidates:
            dc = min(max(abs(nx - tx) - 0, 0) + max(abs(ny - ty) - 0, 0) for tx, ty in candidates)
            # Use Manhattan for simpler deterministic scoring:
            dc = min(abs(nx - tx) + abs(ny - ty) for tx, ty in candidates)
        else:
            dc = abs(nx - px) + abs(ny - py)

        # If stepping into opponent territory is possible (may flip), prioritize if not leading.
        flip_bonus = 0
        if (nx, ny) in opp_terr and not leading:
            flip_bonus = -8  # strong preference
        if (nx, ny) in opp_terr and leading:
            flip_bonus = -2  # mild preference

        # Avoid stepping onto our own territory if we're far from candidates (reduces dithering).
        own_pen = 0
        if (nx, ny) in my_terr and candidates and dc > 2:
            own_pen = 1

        # Keep moving: prefer moves that change position unless stuck.
        move_pen = 0 if (dx, dy) != (0, 0) else 1

        # If not leading, approach opponent; if leading, keep distance while still contesting.
        dist_op = abs(nx - px) + abs(ny - py)
        opp_term = dist_op if leading else -dist_op

        val = (dc, opp_term, own_pen, move_pen, flip_bonus, dx, dy)
        if best is None or val < best[0]:
            best = (val, (dx, dy))

    if best is None:
        return [0, 0]
    dx, dy = best[1]
    return [int(dx), int(dy)]