def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = str(observation.get("self_role", "") or "").lower()
    is_evader = ("evad" in self_role) or ("escape" in self_role) or ("runner" in self_role) or ("flee" in self_role)

    def dist2(x, y, a, b):
        dx, dy = x - a, y - b
        return dx * dx + dy * dy

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    bestv = None

    far_corner = max([(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)], key=lambda c: dist2(c[0], c[1], ox, oy))

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        d_to_opp = dist2(nx, ny, ox, oy)
        man_opp = abs(nx - ox) + abs(ny - oy)

        # Obstacle proximity penalty/bonus
        prox = 0
        for ex, ey in obstacles:
            d = abs(nx - ex) + abs(ny - ey)
            if d == 0:
                prox += 10**9
            else:
                # Prefer not to get adjacent when evading; allow when pursuing but still avoid getting stuck
                if is_evader:
                    prox += max(0, 3 - d) * 25
                else:
                    prox += max(0, 2 - d) * 15

        # Light anti-zigzag: prefer continuing direction if not improving too much
        dir_hint = 0
        if observation.get("self_path") is False or observation.get("self_path") is None:
            pass
        else:
            # deterministic fallback: no path usage (schema says included each turn = False typically)
            pass

        if is_evader:
            # Maximize escape while drifting toward farthest corner to stay away from pursuer
            dc = dist2(nx, ny, far_corner[0], far_corner[1])
            v = d_to_opp * 3 + dc - man_opp - prox
        else:
            # Pursue: minimize distance and reduce Manhattan; prefer tighter approach
            v = -d_to_opp * 3 - man_opp - prox

        if best is None or v > bestv:
            bestv = v
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]