def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
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
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    # Target choice: maximize winning margin; prefer resources I can reach sooner.
    best_res = None
    best_key = None
    for rx, ry in resources:
        myd = cheb((sx, sy), (rx, ry))
        opd = cheb((ox, oy), (rx, ry))
        if myd == 0:
            return [0, 0]
        margin = opd - myd  # positive => I am closer/equal soonest
        # Prefer bigger margin; then smaller my distance; then deterministic coordinate tie-break.
        key = (-(margin), myd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_res = (rx, ry)

    tx, ty = best_res

    def step_score(nx, ny):
        if (nx, ny) in obstacles:
            return (10**9, 10**9, 10**9)
        # Primary: get closer to target.
        myd = cheb((nx, ny), (tx, ty))
        # Secondary: still keep advantage over opponent if possible.
        opd = cheb((ox, oy), (tx, ty))
        margin = opd - myd
        # Tertiary deterministic: prefer staying away from obstacles is naturally handled by invalid moves.
        return (-margin, myd, nx + 31 * ny)

    best_move = (0, 0)
    best_step = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h:
            key = step_score(nx, ny)
            if best_step is None or key < best_step:
                best_step = key
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]