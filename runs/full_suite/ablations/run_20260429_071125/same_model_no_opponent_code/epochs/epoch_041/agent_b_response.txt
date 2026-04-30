def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_move = (0, 0)
    best_val = -10**18

    # Opportunistic policy:
    # - If we can beat opponent on some resource (by cheb distance), head for the best one.
    # - Otherwise, still move toward a resource but add an "interference" term (reduce opponent progress).
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            val = -10**14
        else:
            if not resources:
                # No listed resources: retreat from opponent and move toward center-ish to avoid easy capture.
                cx, cy = (w - 1) // 2, (h - 1) // 2
                val = 2 * cheb(nx, ny, cx, cy) - cheb(nx, ny, ox, oy)
            else:
                val = -cheb(nx, ny, ox, oy) * 0.15  # slight safety
                for rx, ry in resources:
                    d_me = cheb(nx, ny, rx, ry)
                    d_op = cheb(ox, oy, rx, ry)
                    # Prefer resources we can likely reach first; penalize those opponent likely secures.
                    win = 1 if d_me < d_op else 0
                    tie = 1 if d_me == d_op else 0
                    # Interference: moving closer to a contested resource also helps deny opponent tempo.
                    contested = 1 if d_op <= d_me + 1 else 0
                    # Small obstacle proximity penalty (discourages paths that skirt obstacles).
                    near_obs = 0
                    for ax in (nx - 1, nx, nx + 1):
                        for ay in (ny - 1, ny, ny + 1):
                            if (ax, ay) in obstacles:
                                near_obs += 1
                    obstacle_pen = near_obs * 0.06

                    # Main shaping:
                    # - closer to resource is better
                    # - beating opponent is much better
                    # - contested resources get extra "interference" reward
                    r = -d_me * 1.4
                    r += (18.0 if win else (-10.0 if d_op < d_me else 0.0))
                    r += 2.5 * tie
                    r += (3.5 * contested) * (d_op - d_me) * 0.15
                    r -= obstacle_pen

                    val += r
                # Normalize by count to avoid huge magnitudes; deterministic.
                val /= len(resources)

        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]