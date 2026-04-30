def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return (dx * dx + dy * dy)  # squared

    # If on resource, stay to secure it
    for rx, ry in resources:
        if rx == sx and ry == sy:
            return [0, 0]

    # Target selection: prefer resources where we are closer than opponent
    best = None
    best_key = None
    for rx, ry in resources:
        d_self = dist((sx, sy), (rx, ry))
        d_opp = dist((ox, oy), (rx, ry))
        closer = 1 if d_self < d_opp else 0
        # Key: maximize closeness advantage, then minimize our distance, then tie-break by position
        key = (closer, -d_self, -(rx * 9 + ry))
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        # No resources known: drift away from opponent while staying safe
        tx, ty = sx, sy
    else:
        tx, ty = best

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    options = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        base = dist((nx, ny), (tx, ty))
        # Strong penalty if moving close to opponent
        man = abs(nx - ox) + abs(ny - oy)
        opp_pen = 0
        if man == 0:
            opp_pen = 10**6
        elif man == 1:
            opp_pen = 5000
        elif man == 2:
            opp_pen = 500
        # Mild preference to reduce oscillation: prefer moves that keep moving toward target
        toward = 0
        if best is not None:
            toward = dist((sx, sy), (tx, ty)) - dist((nx, ny), (tx, ty))
        score = base + opp_pen - toward * 5
        options.append((score, dx, dy))

    if not options:
        return [0, 0]

    options.sort()
    _, dx, dy = options[0]
    return [int(dx), int(dy)]