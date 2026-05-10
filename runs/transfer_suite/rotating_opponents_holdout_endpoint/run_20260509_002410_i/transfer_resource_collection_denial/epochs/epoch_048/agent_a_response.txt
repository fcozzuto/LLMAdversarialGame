def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def d(a, b):
        ax, ay = a
        bx, by = b
        return abs(ax - bx) + abs(ay - by)

    # Pick a target resource where we can arrive earlier than the opponent (when possible)
    best_r = None
    best_key = None
    for r in resources:
        drs = d((sx, sy), r)
        dro = d((ox, oy), r)
        # earlier arrival first; then closer; then deterministic coordinate tie-break
        key = (drs <= dro, -drs, dro - drs, -r[1], -r[0])
        if best_key is None or key > best_key:
            best_key = key
            best_r = r

    rx, ry = best_r

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Prefer picking up if possible
        pickup_bonus = 0
        if (nx, ny) == (rx, ry):
            pickup_bonus = 10000

        # Encourage moving toward our target while keeping lead vs opponent
        mydist = d((nx, ny), (rx, ry))
        opdist = d((ox, oy), (rx, ry))
        lead = opdist - mydist

        # Slightly avoid stepping near opponent (resource_denier style)
        opp_prox = -max(0, 6 - d((nx, ny), (ox, oy)))

        val = pickup_bonus + 10 * lead - 2 * mydist + opp_prox
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]