def choose_move(observation):
    gw = int(observation["grid_width"])
    gh = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])

    obstacles = {(int(p[0]), int(p[1])) for p in (observation["obstacles"] or [])}
    resources = [(int(r[0]), int(r[1])) for r in (observation["resources"] or [])]
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    scored = []
    for rx, ry in resources:
        if not inb(rx, ry) or (rx, ry) in obstacles:
            continue
        ds = manh(sx, sy, rx, ry)
        do = manh(ox, oy, rx, ry)
        # Prefer resources we are at least as close to; otherwise still chase but heavily penalize
        comp = 40 if ds <= do else -20
        # Also prefer closer resources overall
        score = comp + (40 - ds) - 0.3 * do
        scored.append((score, ds, do, rx, ry))
    if not scored:
        return [0, 0]
    scored.sort(reverse=True)
    _, _, _, tx, ty = scored[0]

    # If standing on a resource, don't move.
    if (sx, sy) == (tx, ty):
        return [0, 0]

    best = (None, -10**18)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        ds2 = manh(nx, ny, tx, ty)
        do2 = manh(ox, oy, tx, ty)
        comp = 40 if ds2 <= do2 else -20
        score = comp + (40 - ds2) - 0.2 * do2
        # Small deterministic tie-break: prefer moves with smaller abs(dx)+abs(dy) then lexicographic
        score -= 0.01 * (abs(dx) + abs(dy))
        if score > best[1]:
            best = ((dx, dy), score)
    if best[0] is None:
        return [0, 0]
    dx, dy = best[0]
    return [int(dx), int(dy)]