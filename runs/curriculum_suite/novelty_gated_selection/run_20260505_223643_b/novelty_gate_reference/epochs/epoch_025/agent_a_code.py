def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    res = observation.get("resources", []) or []
    obs = observation.get("obstacles", []) or []
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    obstacles = {(int(x), int(y)) for x, y in obs}
    resources = [(int(x), int(y)) for x, y in res]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist_cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def pick_best_resource():
        if not resources:
            return None
        best_r = resources[0]
        best_s = -10**18
        for rx, ry in resources:
            ds = dist_cheb(sx, sy, rx, ry)
            do = dist_cheb(ox, oy, rx, ry)
            s = (do - ds) * 1000 - (ds * 3) + (rx + ry) * 0.001  # deterministic tie-break
            if s > best_s:
                best_s = s
                best_r = (rx, ry)
        return best_r

    target = pick_best_resource()
    if target is None:
        # fallback: move toward center while avoiding obstacles
        cx, cy = w // 2, h // 2
        best_move = (0, 0)
        best = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            s = -dist_cheb(nx, ny, cx, cy) - (dist_cheb(nx, ny, ox, oy) * 0.01)
            if s > best:
                best = s
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    tx, ty = target

    # Greedy step toward the chosen resource, but evaluate all moves deterministically.
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        ds_next = dist_cheb(nx, ny, tx, ty)
        do_here = dist_cheb(ox, oy, tx, ty)
        # Prefer improving our lead on the target; small tie-break toward center and away from opponent.
        score = (do_here - ds_next) * 1000 - ds_next * 2 - dist_cheb(nx, ny, ox, oy) * 0.01 - (nx + ny) * 1e-4
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]