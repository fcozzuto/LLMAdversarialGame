def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    role = observation.get("self_role", "pursuer")
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if role == "pursuer":
        # Aim for a point between opponent and the corner closest to opponent (common evader destination)
        oc = min(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
        tx = (ox + oc[0]) / 2.0
        ty = (oy + oc[1]) / 2.0
        best = None
        best_move = [0, 0]
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
                    continue
                # Score favors: reducing distance to opponent (intercept), and steering toward mid-point,
                # with a mild bias to cut corners quickly.
                d_opp = abs(nx - ox) + abs(ny - oy)
                d_mid = abs(nx - tx) + abs(ny - ty)
                d_corner = abs(nx - oc[0]) + abs(ny - oc[1])
                score = d_opp * 2.2 + d_mid * 1.3 + d_corner * 0.2
                if best is None or score < best:
                    best = score
                    best_move = [dx, dy]
        return best_move
    else:
        # Evader: move away from pursuer while drifting toward the corner farthest from pursuer,
        # but keep away from obstacles using a local penalty.
        pc = min(corners, key=lambda c: abs(c[0] - sx) + abs(c[1] - sy))
        target = max(corners, key=lambda c: abs(c[0] - sx) + abs(c[1] - sy))
        best = None
        best_move = [0, 0]
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
                    continue
                d_away = abs(nx - sx) + abs(ny - sy)  # placeholder keeps determinism; not used directly
                d_from_purs = abs(nx - ox) + abs(ny - oy)  # ox,oy is pursuer position when self is evader
                d_target = abs(nx - target[0]) + abs(ny - target[1])
                # Local wall-running: if near a boundary, prefer moves that stay on boundary by reducing drift away.
                boundary = min(nx, w - 1 - nx) + min(ny, h - 1 - ny)
                score = (-d_from_purs) * 2.5 + d_target * 0.9 + boundary * 0.1
                # Obstacle proximity penalty (radius 1)
                prox = 0
                for ax in (-1, 0, 1):
                    for ay in (-1, 0, 1):
                        px, py = nx + ax, ny + ay
                        if (px, py) in obstacles:
                            prox += 1
                score += prox * 1.2
                if best is None or score < best:
                    best = score
                    best_move = [dx, dy]
        return best_move