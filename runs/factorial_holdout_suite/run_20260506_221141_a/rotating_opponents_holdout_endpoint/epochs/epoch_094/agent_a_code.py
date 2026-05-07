def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Choose a target that we can reach first; if not, pick one that least favors the opponent.
    best = None
    best_key = None
    for x, y in resources:
        d_me = cheb(sx, sy, x, y)
        d_op = cheb(ox, oy, x, y)
        # Primary: win the race. Secondary: maximize advantage. Tertiary: prefer closer to us.
        key = (d_me <= d_op, d_op - d_me, -d_me)
        # Deterministic tie-break: fixed ordering by coordinates.
        key = (key[0], key[1], key[2], -x, -y)
        if best_key is None or key > best_key:
            best_key = key
            best = (x, y)
    tx, ty = best

    # Move one step toward target, avoiding obstacles when possible.
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                d = cheb(nx, ny, tx, ty)
                # Prefer reducing distance to target, then staying away from opponent.
                opp = cheb(nx, ny, ox, oy)
                candidates.append((d, -opp, dx, dy))
    if not candidates:
        return [0, 0]
    candidates.sort(reverse=True, key=lambda t: (-t[0], t[1], -t[2], -t[3]))
    # candidates elements are (d, -opp, dx, dy); sort key above ensures deterministic best.
    _, _, dx, dy = candidates[0]
    return [int(dx), int(dy)]