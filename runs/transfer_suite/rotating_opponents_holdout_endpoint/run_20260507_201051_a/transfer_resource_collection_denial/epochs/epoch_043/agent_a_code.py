def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
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
    if not resources:
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Pick a resource we can plausibly beat; otherwise pick the closest resource.
    best = None
    best_score = 10**9
    beaten_exists = False
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        if ds <= do - 1:
            beaten_exists = True
            # Lower is better: prefer win + shorter path; also slight tie-break for distance to prevent dithering.
            score = ds - 0.6 * do
        else:
            # If we can't win, delay but avoid far resources.
            score = ds + 1.2 * max(0, do - ds)
        if score < best_score:
            best_score = score
            best = (rx, ry)

    if beaten_exists:
        # Re-select among beaten resources more strictly if possible.
        best2 = None
        best2_score = 10**9
        for rx, ry in resources:
            ds = man(sx, sy, rx, ry)
            do = man(ox, oy, rx, ry)
            if ds <= do - 1:
                score = ds + 0.2 * do
                if score < best2_score:
                    best2_score = score
                    best2 = (rx, ry)
        if best2 is not None:
            best = best2

    tx, ty = best

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_move_score = 10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        ds_next = man(nx, ny, tx, ty)
        do_next = man(ox, oy, tx, ty)
        # Move to reduce our distance to target, and if possible keep ahead of opponent.
        score = ds_next - 0.7 * do_next + 0.05 * (man(nx, ny, sx, sy))
        # If adjacent to target, strongly prefer capturing it.
        if man(nx, ny, tx, ty) == 0:
            score -= 1000
        if score < best_move_score:
            best_move_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]