def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    def pt(p):
        if isinstance(p, dict):
            if "position" in p:
                p = p["position"]
            if "x" in p and "y" in p:
                return int(p["x"]), int(p["y"])
        return int(p[0]), int(p[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obst = set()
    for p in observation.get("obstacles") or []:
        x, y = pt(p)
        if inb(x, y):
            obst.add((x, y))

    resources = [pt(r) for r in (observation.get("resources") or [])]
    if not resources:
        for dx, dy in [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obst:
                return [dx, dy]
        return [0, 0]

    def man(a, b, x, y):
        dx = a - x
        if dx < 0:
            dx = -dx
        dy = b - y
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue

        # Big reward if we step onto a visible resource.
        on_res = 1 if (nx, ny) in set(resources) else 0

        # Prefer states where we are relatively closer than the opponent for many nearby resources.
        # Also penalize letting the opponent be closer overall.
        score = 0
        for rx, ry in resources:
            d_self = man(nx, ny, rx, ry)
            d_opp = man(ox, oy, rx, ry)
            # self action effectiveness; nearer resources count more.
            score += (d_opp - d_self) / (d_self + 1)
            # If opponent is already extremely close to that resource, heavily discount.
            if d_opp == 0 and d_self > 0:
                score -= 5

        score += 10 * on_res

        # Small tie-break: reduce our distance to the closest resource while increasing distance to opponent.
        closest_self = min(man(nx, ny, rx, ry) for rx, ry in resources)
        opp_closest = min(man(ox, oy, rx, ry) for rx, ry in resources)
        score += (opp_closest - closest_self) * 0.2

        if best is None or score > best[0] or (score == best[0] and (nx, ny) != (sx, sy)):
            best = (score, dx, dy)

    if best is None:
        return [0, 0]
    return [best[1], best[2]]