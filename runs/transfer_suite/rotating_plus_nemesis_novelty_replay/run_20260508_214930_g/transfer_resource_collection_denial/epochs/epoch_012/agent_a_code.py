def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    env = observation.get("environment_name", "")

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        return [0, 0]

    # Select a target resource to win the race on (maximize opponent distance advantage).
    best = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        oppd = cheb(ox, oy, rx, ry)
        # Prefer resources where I am not farther; otherwise still pick near ones.
        win_margin = (oppd - myd)
        # Tie-break: prefer smaller my distance, then more central.
        center_dist = cheb(rx, ry, w // 2, h // 2)
        key = (win_margin, -myd, -center_dist, -(rx + 2 * ry))
        if best is None or key > best[0]:
            best = (key, rx, ry, myd, oppd)
    _, tx, ty, myd0, oppd0 = best

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        myd = cheb(nx, ny, tx, ty)
        oppd = cheb(ox, oy, tx, ty)
        # Move scoring:
        # 1) improve my progress to target,
        # 2) increase race advantage (oppd - myd),
        # 3) slightly avoid positions where opponent is closer to me (interception pressure),
        # 4) opportunistically reduce opponent distance to target if it is currently winning against me.
        race = oppd - myd
        progress = (myd0 - myd)
        opp_to_me = cheb(ox, oy, nx, ny)
        block = 0
        if oppd0 > myd0:
            block = (oppd0 - oppd)  # keep opp from getting too close to its likely target

        # If on resource, strongly commit.
        on_resource = 1 if (nx, ny) == (tx, ty) else 0
        score = (10 * on_resource + 3 * race + 2 * progress - 0.05 * opp_to_me + 0.5 * block, -(dx * dx + dy * dy))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]