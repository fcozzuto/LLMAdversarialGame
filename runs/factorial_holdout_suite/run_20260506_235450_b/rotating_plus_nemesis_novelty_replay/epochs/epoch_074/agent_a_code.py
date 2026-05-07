def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    ox, oy = observation.get("opponent_position", (None, None))
    opp_exists = ox is not None and oy is not None

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        # Chebyshev approximates shortest turns with diagonal moves
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    # Pick best resource by maximizing how much sooner we can reach it than opponent
    best = None  # (score_tuple, target)
    if resources:
        for r in resources:
            tx, ty = r[0], r[1]
            if (tx, ty) in obstacles:
                continue
            sd = dist((sx, sy), (tx, ty))
            if opp_exists:
                od = dist((ox, oy), (tx, ty))
                score = (od - sd, -sd)  # first: advantage; second: smaller distance
            else:
                score = (-sd, sd)
            if best is None or score > best[0]:
                best = (score, (tx, ty))

    if best is None:
        # No usable resources: move to center while avoiding immediate obstacles
        cx, cy = (w - 1) // 2, (h - 1) // 2
        choices = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if not inb(nx, ny) or (nx, ny) in obstacles:
                    continue
                choices.append((-(abs(nx - cx) + abs(ny - cy)), dx, dy))
        if choices:
            choices.sort(reverse=True)
            return [choices[0][1], choices[0][2]]
        return [0, 0]

    tx, ty = best[1]

    # Greedy one-step toward target with obstacle avoidance
    dx_raw = 0 if tx == sx else (1 if tx > sx else -1)
    dy_raw = 0 if ty == sy else (1 if ty > sy else -1)

    candidates = []
    for dx in (dx_raw, 0, -dx_raw):
        for dy in (dy_raw, 0, -dy_raw):
            dx = 0 if dx not in (-1, 0, 1) else dx
            dy = 0 if dy not in (-1, 0, 1) else dy
            nx, ny = sx + dx, sy + dy
            if (nx, ny) == (sx, sy):
                # allow staying, but deprioritize
                pass
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            # Prefer moves that reduce distance to target, and if tied, reduce distance to opponent's position
            nd = dist((nx, ny), (tx, ty))
            if opp_exists:
                od = dist((ox, oy), (nx, ny))
                score = (-nd, -od if (nx, ny) != (sx, sy) else -10**9)
            else:
                score = (-nd, 0)
            if (dx, dy) == (0, 0):
                score = (score[0] - 0.1, score[1])
            candidates.append((score, dx, dy))

    if candidates:
        candidates.sort(reverse=True)
        return [candidates[0][1], candidates[0][2]]
    return [0, 0]