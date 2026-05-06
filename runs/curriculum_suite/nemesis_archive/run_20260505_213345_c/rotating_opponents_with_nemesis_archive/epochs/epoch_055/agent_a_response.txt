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

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = -10**18

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b, c, d):
        dx = a - c
        dy = b - d
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx + dy

    # Target scoring: prefer resources where we are closer than opponent,
    # and avoid giving opponent easy "row capture" (penalize resources on opponent row).
    opp_row = oy
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        # Heuristic for this move: best achievable advantage over all resources
        move_val = -10**18
        for rx, ry in resources:
            sd = dist(nx, ny, rx, ry)
            od = dist(ox, oy, rx, ry)

            # If resource lies on opponent's current row, it's likely contested by sweep behavior
            row_pen = 0
            if ry == opp_row:
                row_pen = 3.0

            # If opponent is already very close, deprioritize
            close_opp_pen = 0
            if od <= 2:
                close_opp_pen = 2.0

            # Advantage: higher means better for us
            adv = (od - sd) - row_pen - close_opp_pen
            # Mild preference to reduce travel time among comparable advantages
            adv -= 0.05 * sd
            if adv > move_val:
                move_val = adv

        # Small tie-break: prefer staying closer to the resource set centroid roughly
        # (deterministic, cheap), using average resource positions.
        if move_val > best_val:
            best_val = move_val
            best_move = [dx, dy]

    return best_move