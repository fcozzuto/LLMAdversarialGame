def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role", "") or "").lower()
    pursuer = any(k in role for k in ("pursuer", "hunter", "chaser", "pursuit"))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_sc = None

    def clamp(nx, ny):
        if nx < 0: nx = 0
        elif nx >= w: nx = w - 1
        if ny < 0: ny = 0
        elif ny >= h: ny = h - 1
        return nx, ny

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Corner targets (for evader), deterministic order
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if not pursuer:
        # Prefer the corner farthest from opponent (evader goal)
        tcx, tcy = max(corners, key=lambda t: man(t[0], t[1], ox, oy))
    else:
        # For pursuer, prefer reducing both coordinates distance
        tcx, tcy = ox, oy

    for dx, dy in moves:
        nx, ny = clamp(sx + dx, sy + dy)
        # If obstacle, engine would keep in place; heavily penalize landing there
        occ = (nx, ny) in obstacles
        d = man(nx, ny, ox, oy)

        # Base objective
        sc = -d if pursuer else d

        # Obstacle and "stall" penalties
        if occ:
            sc -= 10**6 if pursuer else -10**6
        if nx == sx and ny == sy and not occ:
            sc -= 1 if pursuer else -1

        # Additional shaping: pursue along coordinate alignment; evade toward corner with tie-break
        if pursuer:
            before = man(sx, sy, ox, oy)
            after = d
            sc += (after < before) * 2 - (after > before) * 2
            # Encourage moves that reduce dx and dy components (Manhattan decomposition)
            sc += (abs(ox - nx) < abs(ox - sx)) * 0.6
            sc += (abs(oy - ny) < abs(oy - sy)) * 0.6
        else:
            # Move toward farthest corner, but keep distance from opponent primary
            dist_corner = man(nx, ny, tcx, tcy)
            dist_corner_now = man(sx, sy, tcx, tcy)
            sc += (dist_corner_now - dist_corner) * 0.15
            # Avoid stepping closer to opponent diagonally too much
            sc += (man(nx, ny, ox, oy) - man(sx, sy, ox, oy)) * 0.1

        if best_sc is None or sc > best_sc:
            best_sc = sc
            best = [dx, dy]

    return best if best is not None else [0, 0]