def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    oset = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                oset.add((x, y))

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in oset

    self_role = str(observation.get("self_role", "") or "")
    is_evader = ("evader" in self_role.lower()) or ("evasion" in str(observation.get("environment_name", "")).lower())
    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    # Prefer not to step onto opponent when capture_radius=0
    def d_after(nx, ny):
        return abs(nx - ox) + abs(ny - oy)

    # Small heuristic: prefer moving away/toward nearest corner depending on role
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    def corner_score(nx, ny):
        # evader: larger min distance from any corner; pursuer: smaller
        md = min(abs(nx - cx) + abs(ny - cy) for cx, cy in corners)
        return md

    # Deterministic tie-breaking order
    # Candidate ordering by (dx,dy) ensures stability
    cand.sort(key=lambda t: (t[0], t[1]))

    best = None
    if is_evader:
        best_val = -10**9
        for dx, dy, nx, ny in cand:
            if nx == ox and ny == oy:
                val = -10**8
            else:
                val = d_after(nx, ny) * 10 + corner_score(nx, ny)
            if val > best_val:
                best_val = val
                best = [dx, dy]
    else:
        best_val = 10**9
        for dx, dy, nx, ny in cand:
            val = d_after(nx, ny)
            # slight preference for approaching while not colliding
            if nx == ox and ny == oy:
                val -= 0.1
            if val < best_val:
                best_val = val
                best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]