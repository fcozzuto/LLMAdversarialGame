def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles_in = observation.get("obstacles") or []

    obstacles = set()
    for p in obstacles_in:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        return [0, 0]

    # Choose target that maximizes opponent disadvantage (race): (opp_dist - self_dist)
    best_t = None
    best_key = None
    for r in resources:
        tx, ty = int(r[0]), int(r[1])
        if not inside(tx, ty) or blocked(tx, ty):
            continue
        sd = man(sx, sy, tx, ty)
        od = man(ox, oy, tx, ty)
        # Prefer targets we can reach at least as fast; then best race gap; then closer to ourselves.
        key = (1 if sd <= od else 0, (od - sd), -sd, -abs(ty - sy), -abs(tx - sx))
        if best_key is None or key > best_key:
            best_key = key
            best_t = (tx, ty)
    if best_t is None:
        return [0, 0]

    tx, ty = best_t
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best_move = [0, 0]
    best_mkey = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or blocked(nx, ny):
            continue
        nd = man(nx, ny, tx, ty)
        od_now = man(ox, oy, tx, ty)
        sd_now = man(sx, sy, tx, ty)
        # Prefer moves that improve our race gap; small tie-breakers to reduce oscillation.
        race_gap = od_now - nd
        move_key = (race_gap, -nd, -abs(ny - sy), -abs(nx - sx))
        if best_mkey is None or move_key > best_mkey:
            best_mkey = move_key
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]