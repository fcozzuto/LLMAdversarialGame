def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        # No visible resources: go to safer central drift that also increases distance from opponent slightly.
        tx = 0 if sx < w // 2 else w - 1
        ty = 0 if sy < h // 2 else h - 1
        tx = (tx + (w - 1 - ox)) // 2
        ty = (ty + (h - 1 - oy)) // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        if inb(sx + dx, sy + dy) and (sx + dx, sy + dy) not in obstacles:
            return [dx, dy]
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    # Choose target where we are relatively earlier than opponent; otherwise fall back to nearest.
    best_target = resources[0]
    best_key = None
    for (rx, ry) in resources:
        my = cheb(sx, sy, rx, ry)
        op = cheb(ox, oy, rx, ry)
        # Prefer large lead; if tie, prefer smaller my distance; then deterministic coordinate.
        key = (op - my, -my, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best_target = (rx, ry)

    rx, ry = best_target
    # Evaluate legal moves by resulting improvement toward target and ensuring we don't walk into obstacles.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        my_now = cheb(sx, sy, rx, ry)
        my_next = cheb(nx, ny, rx, ry)
        op_next = cheb(ox, oy, rx, ry)
        # Primary: reduce distance to target; Secondary: keep advantage if possible; Tertiary: deterministic.
        val = (my_now - my_next) * 1000 + (op_next - my_next) * 10 - (abs(dx) + abs(dy))
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]