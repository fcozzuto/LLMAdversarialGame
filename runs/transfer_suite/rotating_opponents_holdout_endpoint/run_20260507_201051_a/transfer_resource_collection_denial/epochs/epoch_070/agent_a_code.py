def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def clamp_move(dx, dy):
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return nx, ny
        return sx, sy

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves = sorted(moves, key=lambda t: (t[0] == 0 and t[1] == 0, t[0], t[1]))  # deterministic order

    if not resources:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda c: dist((sx, sy), c) - 2 * dist((ox, oy), c))
        best = [0, 0]
        best_sc = -10**18
        for dx, dy in moves:
            nx, ny = clamp_move(dx, dy)
            sc = dist((nx, ny), (tx, ty)) - 0.5 * dist((nx, ny), (ox, oy))
            if sc > best_sc:
                best_sc = sc
                best = [dx, dy]
        return best

    # Opportunistic: pick the move that creates the strongest "first-collection" advantage
    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = clamp_move(dx, dy)
        # If we can step directly onto a resource, heavily prioritize it
        step_resource = 1 if (nx, ny) in obstacles else 0
        best_adv_for_move = -10**18
        for rx, ry in resources:
            ts = dist((nx, ny), (rx, ry))
            to = dist((ox, oy), (rx, ry))
            # Lower ts is good; higher to is good; slight tie-break to closer-now
            adv = (to - ts) * 2 - ts * 0.15
            if (rx, ry) == (nx, ny):
                adv += 50
            if adv > best_adv_for_move:
                best_adv_for_move = adv
        # Secondary objective: keep us away from obstacles less (use local feasibility as already filtered)
        # Tertiary objective: slightly maximize distance from opponent to reduce contest (shadow opponent)
        safety = -0.05 * dist((nx, ny), (ox, oy))
        score = best_adv_for_move + safety - step_resource
        if score > best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move