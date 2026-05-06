def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set(obstacles)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best = [0, 0]
    bestv = -10**18

    target = None
    if resources:
        target = resources[0]
        for r in resources[1:]:
            if cheb(x, y, r[0], r[1]) < cheb(x, y, target[0], target[1]):
                target = r

    tx, ty = (w - 1, h - 1) if not target else (target[0], target[1])

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue
        if resources:
            v = -cheb(ox, oy, nx, ny) * 5
            closest_self = 10**9
            closest_opp = 10**9
            for rx, ry in resources:
                ds = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                if ds < closest_self:
                    closest_self = ds
                if do < closest_opp:
                    closest_opp = do
            v += (closest_opp - closest_self) * 20
            v -= (abs(nx - tx) + abs(ny - ty)) * 2
        else:
            v = -cheb(nx, ny, w - 1, h - 1) * 10
        if v > bestv:
            bestv = v
            best = [dx, dy]

    return best