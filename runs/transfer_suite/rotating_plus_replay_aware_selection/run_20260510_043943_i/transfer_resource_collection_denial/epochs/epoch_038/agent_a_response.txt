def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set(tuple(p) for p in obs_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obstacles)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(a, b, c, d):
        x = a - c
        if x < 0:
            x = -x
        y = b - d
        if y < 0:
            y = -y
        return x + y

    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue

        if resources:
            move_score = -10**18
            for rx, ry in resources:
                ds = man(nx, ny, rx, ry)
                do = man(ox, oy, rx, ry)
                # race pressure (win more than approach)
                val = (do - ds) * 200 - ds * 3 - do
                if ds == 0:
                    val += 10**7
                elif ds == 1:
                    val += 10**5
                elif ds == 2:
                    val += 10**3
                move_score = val if val > move_score else move_score
        else:
            # no resources: drift away from opponent to reduce contest, else stay
            myd = man(nx, ny, ox, oy)
            move_score = myd

        if move_score > best_score:
            best_score = move_score
            best_move = [dx, dy]

    return best_move