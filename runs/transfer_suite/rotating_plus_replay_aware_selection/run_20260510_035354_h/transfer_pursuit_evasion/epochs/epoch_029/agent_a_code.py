def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        try:
            obs.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    evade = ("evad" in role) or ("purs" not in role and "evad" in opp_role)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]

    def best_corner_dist(x, y):
        return min(abs(x - cx) + abs(y - cy) for cx, cy in corners)

    best = [0, 0]
    best_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue

        d = abs(nx - ox) + abs(ny - oy)

        # Primary: increase distance when evading; decrease when pursuing.
        primary = d if evade else -d

        # Secondary: for stability vs corner-based evasion, prefer moves that are "better" corners
        # for evader (farthest from corners) and "worse" corners for pursuer (approach nearest corner).
        cdist = best_corner_dist(nx, ny)
        secondary = cdist if evade else -cdist

        # Tertiary: tie-break deterministically to avoid oscillation; slight preference for diagonal then orthogonal.
        diag = 1 if dx != 0 and dy != 0 else 0
        tertiary = -diag  # smaller first: prefer diagonal

        # Additional obstacle nudge: avoid stepping into cells with many obstacle neighbors.
        neigh = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if 0 <= tx < w and 0 <= ty < h and (tx, ty) in obs:
                    neigh += 1
        quad = -neigh if evade else neigh  # evader avoids crowded; pursuer prefers crowded (to trap)

        key = (primary, secondary, tertiary, quad, -abs(dx) - abs(dy))
        if best_key is None or key > best_key:
            best_key = key
            best = [dx, dy]

    return best