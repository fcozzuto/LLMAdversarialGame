def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obst = set()
    for a in obstacles:
        try:
            x, y = a
            obst.add((int(x), int(y)))
        except Exception:
            pass

    deltas = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1), (0, 0), (0, 1),
              (1, -1), (1, 0), (1, 1)]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = [0, 0]
    best_key = (-10**18, 10**18, 10**18)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obst:
            continue
        if not resources:
            # no resources known: slow pivot away from opponent, while staying safe
            key = (md(nx, ny, ox, oy), -md(nx, ny, sx, sy), 0)
            if key > (best_key[0], -best_key[2], best_key[2]):
                best, best_key = [dx, dy], (key[0], 0, 0)
            continue

        best_res = None
        best_res_key = None
        for r in resources:
            try:
                rx, ry = r
            except Exception:
                continue
            rx, ry = int(rx), int(ry)
            d_self = md(nx, ny, rx, ry)
            d_opp = md(ox, oy, rx, ry)

            # Favor resources where we can arrive no slower; otherwise still minimize loss potential.
            # Key: maximize advantage (opp - self), then minimize our distance, then minimize opponent distance.
            adv = d_opp - d_self
            key = (adv, -d_self, -d_opp)
            if best_res_key is None or key > best_res_key:
                best_res_key = key
                best_res = (rx, ry, d_self, d_opp)

        # Secondary safety: don't move closer to obstacles indirectly is hard; just keep distance from opponent if tie.
        _, self_d, opp_d = best_res[0], best_res[2], best_res[3]
        key = (best_res_key[0], self_d, opp_d)
        if key[0] > best_key[0] or (key[0] == best_key[0] and (key[1] < best_key[1] or (key[1] == best_key[1] and key[2] < best_key[2]))):
            best_key = key
            best = [dx, dy]

    return [int(best[0]), int(best[1])]