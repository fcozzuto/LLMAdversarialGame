def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = str(observation.get("self_role", "")).lower()
    opponent_role = str(observation.get("opponent_role", "")).lower()
    is_evader = ("evader" in self_role) or ("pursuer" in opponent_role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def king_dist(x, y):
        dx = x - ox
        if dx < 0:
            dx = -dx
        dy = y - oy
        if dy < 0:
            dy = -dy
        return dx + dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    # Base target: move to maximize distance if evader, minimize if pursuer.
    # Secondary: prefer moves that improve (or worsen) both axes with deterministic tie-breaking.
    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
        dist = king_dist(nx, ny)

        # Capture is immediate in real rules; avoid being on opponent unless we are pursuer.
        on_top = (nx == ox and ny == oy)
        if on_top and is_evader:
            score = -10**9
        else:
            # Heuristic score: evader wants larger dist, pursuer wants smaller dist.
            score = dist if is_evader else -dist

            # Corner bias to help deterministic "evasion_corner" opponents:
            # evader prefers moving toward the farther corner from pursuer; pursuer prefers opposite.
            far_corner_x = 0 if ox >= (w - 1) / 2 else (w - 1)
            far_corner_y = 0 if oy >= (h - 1) / 2 else (h - 1)
            corner_score = abs(nx - far_corner_x) + abs(ny - far_corner_y)
            if is_evader:
                score += 0.001 * corner_score
            else:
                score += 0.001 * (-corner_score)

        if best_val is None:
            best_val = score
            best_move = (dx, dy)
        else:
            if score > best_val:
                best_val = score
                best_move = (dx, dy)
            elif score == best_val:
                # Deterministic tie-break: prefer lower |dx|+|dy|, then lexicographic dx,dy
                cur_eff = abs(best_move[0]) + abs(best_move[1])
                new_eff = abs(dx) + abs(dy)
                if new_eff < cur_eff or (new_eff == cur_eff and (dx, dy) < best_move):
                    best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]