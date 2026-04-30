def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    if not resources:
        # Go toward opponent side slightly, but avoid obstacles.
        tx, ty = w - 1 if ox < sx else 0, h - 1 if oy < sy else 0
        best_move = (0, 0)
        best_score = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                continue
            score = -cheb(nx, ny, tx, ty)
            if score > best_score:
                best_score = score
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # Choose a target resource: closest for us, but prioritize where we have an edge over opponent.
    # Deterministic tie-breaking by target coordinates.
    best_t = None
    best_key = None
    for tx, ty in resources:
        dm = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        # Key: smaller my distance; larger advantage (do-dm); then deterministic by coords.
        key = (dm, -(do - dm), tx, ty)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (tx, ty)

    tx, ty = best_t
    # Move greedily toward target while avoiding obstacles.
    best_move = (0, 0)
    best_tuple = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        d_me = cheb(nx, ny, tx, ty)
        d_opp = cheb(ox, oy, tx, ty)
        # Prefer decreasing distance to target; if equal, prefer improving advantage; if equal, prefer closer to opponent.
        t = (d_me, -(d_opp - d_me), cheb(nx, ny, ox, oy), dx, dy)
        if best_tuple is None or t < best_tuple:
            best_tuple = t
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]