def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid.append((dx, dy))
    if not valid:
        return [0, 0]

    if not resources:
        tx, ty = gw // 2, gh // 2
        best = None
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            key = (dist((nx, ny), (tx, ty)), abs((nx + ny) - (sx + sy)))
            if best is None or key < best[0]:
                best = (key, (dx, dy))
        return [best[1][0], best[1][1]]

    def opp_greedy_next(px, py, target):
        best_step = (0, 0)
        best_key = None
        for dx, dy in moves:
            nx, ny = px + dx, py + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d = dist((nx, ny), target)
            # tie-break: prefer steps that approach and also not into obstacle-adjacent traps
            trap = 0
            for adx, ady in moves:
                ax, ay = nx + adx, ny + ady
                if inb(ax, ay) and (ax, ay) in obstacles:
                    trap += 1
            key = (d, trap, abs(nx - target[0]) + abs(ny - target[1]))
            if best_key is None or key < best_key:
                best_key = key
                best_step = (dx, dy)
        return px + best_step[0], py + best_step[1]

    best_score = None
    best_move = (0, 0)
    center = (gw // 2, gh // 2)
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        my_step_center = dist((nx, ny), center)
        score = 0
        # consider up to 6 closest resources for speed
        ordered = sorted(resources, key=lambda r: dist((nx, ny), r))[:6]
        for r in ordered:
            my_d = dist((nx, ny), r)
            ax, ay = opp_greedy_next(ox, oy, r)
            opp_d = dist((ax, ay), r)
            # winning race term
            race = (opp_d - my_d)
            # immediate pickup preference
            pickup = 0 if (nx, ny) == r else 0
            # also prefer overall approach if no clear win
            approach = -my_d
            score += 12 * (race) + 2 * approach + 1 * my_step_center * (-0.01) + pickup
        # secondary: prefer reducing distance to nearest remaining resource
        nearest = min(resources, key=lambda r: dist((nx, ny), r))
        score += -0.5 * dist((nx, ny), nearest)
        key = (-(score), dist((nx, ny), center), dx, dy)
        if best_score is None or key < best_score:
            best_score = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]