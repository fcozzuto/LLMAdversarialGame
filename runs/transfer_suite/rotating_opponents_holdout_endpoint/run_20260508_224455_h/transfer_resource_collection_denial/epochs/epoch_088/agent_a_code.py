def choose_move(observation):
    gw = int(observation["grid_width"])
    gh = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    resources = observation.get("resources") or []
    obstacles = {(int(p[0]), int(p[1])) for p in (observation.get("obstacles") or [])}

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def dist8(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    best = None
    best_key = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if (rx, ry) in obstacles or not inb(rx, ry):
            continue
        md = dist8(sx, sy, rx, ry)
        od = dist8(ox, oy, rx, ry)
        key = (od - md, -md, -(rx + 9 * ry), -rx)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        return [0, 0]
    tx, ty = best

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_m = (0, 0)
    best_ms = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        self_d = dist8(nx, ny, tx, ty)
        opp_d = dist8(ox, oy, tx, ty)
        # Prioritize reducing our distance; also keep advantage vs opponent.
        score = (opp_d - self_d, -self_d, -abs(nx - tx) - abs(ny - ty), -nx, -ny)
        if best_ms is None or score > best_ms:
            best_ms = score
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]