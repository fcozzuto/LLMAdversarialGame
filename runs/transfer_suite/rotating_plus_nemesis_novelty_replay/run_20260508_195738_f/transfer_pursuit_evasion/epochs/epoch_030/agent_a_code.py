def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs_set = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs_set

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    role = observation.get("self_role", "") or ""
    our_evader = (role.lower() == "evader")

    # Simple obstacle-aware step choice:
    # - Pursuer: minimize Chebyshev distance to opponent; tie-break by moving in the strongest direction (reduce both axes if possible)
    # - Evader: maximize Chebyshev distance; tie-break by increasing the axis-aligned separation (avoid heading into dead-ends)
    best_move = [0, 0]
    best_key = None

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        d = cheb(nx, ny, ox, oy)
        # Additional preference for diagonal/axis progress
        signx = 0 if ox == nx else (1 if ox > nx else -1)
        signy = 0 if oy == ny else (1 if oy > ny else -1)
        ax_prog = (1 if dx == signx else 0) + (1 if dy == signy else 0)
        # dead-end penalty: count available neighbor moves from candidate
        neigh = 0
        for ddx, ddy in moves:
            tx, ty = nx + ddx, ny + ddy
            if ok(tx, ty):
                neigh += 1

        if our_evader:
            key = (d, ax_prog, neigh, -abs((ox - nx)) - abs((oy - ny)))
            # maximize key
            if best_key is None or key > best_key:
                best_key = key
                best_move = [dx, dy]
        else:
            # prioritize smaller distance; then stronger directional progress; then more mobility
            key = (-d, ax_prog, neigh, -abs((ox - nx)) - abs((oy - ny)))
            if best_key is None or key > best_key:
                best_key = key
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]