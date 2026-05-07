def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs = set((p[0], p[1]) for p in obstacles)

    def man(a, b, c, d):
        x = a - c
        if x < 0:
            x = -x
        y = b - d
        if y < 0:
            y = -y
        return x + y

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Pick top resources by "opponent advantage": how much closer opponent is than us, but bias toward cells we can reach quickly.
    scored = []
    for rx, ry in resources:
        my_d = man(sx, sy, rx, ry)
        op_d = man(ox, oy, rx, ry)
        key = (op_d - my_d, -my_d, -(rx * 9 + ry * 3))
        scored.append((key, rx, ry))
    scored.sort(reverse=True)

    candidates = scored[:min(4, len(scored))]  # keep small and deterministic

    best_move = [0, 0]
    best_val = None

    for _, tx, ty in candidates:
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obs:
                continue
            # Prefer moving closer (Chebyshev) to target; tie-break by making opponent farther (Manhattan).
            self_dist = max(abs(tx - nx), abs(ty - ny))
            op_dist = man(ox, oy, tx, ty)
            # Also estimate opponent distance after our move (still toward same target) to reduce contention locally.
            # Deterministic local estimate: assume opponent takes its best 1-step toward target if available.
            best_op_next = 10**9
            for odx, ody in deltas:
                ex, ey = ox + odx, oy + ody
                if ex < 0 or ex >= w or ey < 0 or ey >= h:
                    continue
                if (ex, ey) in obs:
                    continue
                d = max(abs(tx - ex), abs(ty - ey))
                if d < best_op_next:
                    best_op_next = d
            opp_after = best_op_next

            val = (-self_dist, -(op_dist), -opp_after, (nx - tx) * 0 + (ny - ty) * 0)
            if best_val is None or val > best_val:
                best_val = val
                best_move = [dx, dy]

    return best_move