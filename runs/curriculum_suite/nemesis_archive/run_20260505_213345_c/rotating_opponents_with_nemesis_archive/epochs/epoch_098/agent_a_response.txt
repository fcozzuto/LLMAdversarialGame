def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(a, b):
        dx = a[0] - b[0]
        if dx < 0:
            dx = -dx
        dy = a[1] - b[1]
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy  # Chebyshev

    # Pick a contest target: resource where we are closer than opponent, else nearest resource.
    best_r = None
    best_adv = -10**9
    best_ds = 10**9
    for r in resources:
        ds = dist((sx, sy), r)
        do = dist((ox, oy), r)
        adv = do - ds
        if adv > best_adv or (adv == best_adv and ds < best_ds):
            best_adv, best_ds, best_r = adv, ds, r

    tx, ty = best_r
    # Local choice: among legal moves, pick one that most rapidly reaches target and improves contest margin.
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        ds_next = dist((nx, ny), (tx, ty))
        do = dist((ox, oy), (tx, ty))
        adv_next = do - ds_next
        score = adv_next * 2 - ds_next
        # deterministic tiebreak: prefer staying still last by ordering via score then fixed comparison
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            if (dx, dy) == (0, 0) and best_move != (0, 0):
                continue
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]