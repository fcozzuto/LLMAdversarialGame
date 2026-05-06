def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    def best_resource_score(x, y):
        best = None
        for rx, ry in resources:
            ds = manh(x, y, rx, ry)
            do = manh(ox, oy, rx, ry)
            adv = do - ds  # positive => we are closer than opponent
            # Prefer taking/keeping lead on some resource; then prefer being closer to it; then prefer staying safer
            score = (-adv, ds, -manh(x, y, ox, oy), rx, ry)
            if best is None or score < best:
                best = score
        return best  # tuple

    best_move = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        br = best_resource_score(nx, ny)
        # Primary: maximize lead (via -adv), then minimize ds, then maximize distance from opponent
        # Secondary tie-break: deterministic
        move_key = (br[0], br[1], br[2], dx, dy)
        if best_move is None or move_key < best_move[0]:
            best_move = (move_key, dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[1]), int(best_move[2])]