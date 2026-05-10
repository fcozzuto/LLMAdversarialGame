def choose_move(observation):
    gw = int(observation["grid_width"])
    gh = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    resources = observation.get("resources") or []
    obstacles = {(int(p[0]), int(p[1])) for p in (observation.get("obstacles") or [])}

    def inb(x, y): return 0 <= x < gw and 0 <= y < gh
    def dist8(x1, y1, x2, y2):
        ax, ay = abs(x1 - x2), abs(y1 - y2)
        return ax if ax > ay else ay

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
        # prioritize: advantage over opponent, then faster pickup, then more central, then lower x
        key = (od - md, -(md), -(rx + 9 * ry), -rx)
        if best_key is None or key > best_key:
            best_key, best = key, (rx, ry)

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
        nds = dist8(nx, ny, tx, ty)
        ndo = dist8(nx, ny, ox, oy)
        # tie-break: reduce to target, increase distance from opponent, then prefer diagonal-ish progress
        k = (-(nds), ndo, -(abs(tx - nx) + abs(ty - ny)), -((dx == 0) + (dy == 0)))
        if best_ms is None or k > best_ms:
            best_ms, best_m = k, (dx, dy)

    return [int(best_m[0]), int(best_m[1])]