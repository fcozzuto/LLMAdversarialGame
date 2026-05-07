def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if in_bounds(nx, ny) and (nx, ny) not in blocked:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]
    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Approximate race: opponent gets one greedy step next turn toward the same resource.
    # Their best possible distance after one step (ignoring obstacles) is max(0, d-1).
    best_move = (0, 0)
    best_key = None

    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        # Prefer stepping onto a resource immediately.
        immediate = 0
        for rx, ry in resources:
            if rx == nx and ry == ny:
                immediate = 1
                break

        best_adv = -10**9
        best_own = 10**9
        # Also mildly discourage moves that bring us closer to many resources than the opponent.
        closeness_pen = 0

        for rx, ry in resources:
            our_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            opp_next = opp_d - 1
            if opp_next < 0:
                opp_next = 0
            adv = opp_next - our_d
            if adv > best_adv:
                best_adv = adv
                best_own = our_d
            # Penalize if we're extremely close to multiple resources while opponent is not.
            if our_d <= 2 and opp_next > our_d:
                closeness_pen += 1

        key = (
            immediate,
            best_adv,            # bigger is better
            -best_own,          # smaller our_d is better
            -closeness_pen      # fewer "unsafe closeness" is better
        )
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]